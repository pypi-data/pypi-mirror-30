#    Copyright 2018 Alexey Stepanov aka penguinolog.

#    Copyright 2016 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Python subprocess.Popen wrapper."""

from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import select
import sys
import subprocess  # nosec  # Expected usage
import threading
import time
import typing

import six
import threaded

from exec_helpers import exceptions
from exec_helpers import exec_result
from exec_helpers import _log_templates
from exec_helpers import proc_enums

logger = logging.getLogger(__name__)

_win = sys.platform == "win32"
_type_exit_codes = typing.Union[int, proc_enums.ExitCodes]
_type_expected = typing.Optional[typing.Iterable[_type_exit_codes]]


class SingletonMeta(type):
    """Metaclass for Singleton.

    Main goals: not need to implement __new__ in singleton classes
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Singleton."""
        if cls not in cls._instances:
            cls._instances[cls] = super(
                SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def _py2_str(src):  # pragma: no cover
    """Convert text to correct python type."""
    if not six.PY3 and isinstance(src, six.text_type):
        return src.encode(
            encoding='utf-8',
            errors='strict',
        )
    return src


BaseSingleton = type.__new__(  # noqa
    SingletonMeta,
    _py2_str('BaseSingleton'),
    (object, ),
    {'__slots__': ()}
)


class Subprocess(BaseSingleton):
    """Subprocess helper with timeouts and lock-free FIFO."""

    __slots__ = (
        '__lock',
        '__process',
    )

    def __init__(self):
        """Subprocess helper with timeouts and lock-free FIFO.

        For excluding race-conditions we allow to run 1 command simultaneously
        """
        self.__lock = threading.RLock()
        self.__process = None

    @property
    def lock(self):  # type: () -> threading.RLock
        """Lock.

        :rtype: threading.RLock
        """
        return self.__lock

    def __enter__(self):
        """Context manager usage."""
        self.lock.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager usage."""
        if self.__process:
            self.__process.kill()
        self.lock.release()

    def __del__(self):
        """Destructor. Kill running subprocess, if it running."""
        if self.__process:
            self.__process.kill()

    def __exec_command(
        self,
        command,  # type: str
        cwd=None,  # type: typing.Optional[str]
        env=None,  # type: typing.Optional[typing.Dict[str, typing.Any]]
        timeout=None,  # type: typing.Optional[int]
        verbose=False  # type: bool
    ):
        """Command executor helper.

        :type command: str
        :type cwd: str
        :type env: dict
        :type timeout: int
        :rtype: ExecResult
        """
        def poll_streams(
            result,  # type: exec_result.ExecResult
            stdout,  # type: io.TextIOWrapper
            stderr,  # type: io.TextIOWrapper
        ):
            """Poll streams to the result object."""
            if _win:  # pragma: no cover
                # select.select is not supported on windows
                result.read_stdout(src=stdout, log=logger, verbose=verbose)
                result.read_stderr(src=stderr, log=logger, verbose=verbose)
            else:
                rlist, _, _ = select.select(
                    [stdout, stderr],
                    [],
                    [])
                if rlist:
                    if stdout in rlist:
                        result.read_stdout(
                            src=stdout,
                            log=logger,
                            verbose=verbose
                        )
                    if stderr in rlist:
                        result.read_stderr(
                            src=stderr,
                            log=logger,
                            verbose=verbose
                        )

        @threaded.threaded(started=True, daemon=True)
        def poll_pipes(
            result,  # type: exec_result.ExecResult
            stop  # type: threading.Event
        ):
            """Polling task for FIFO buffers.

            :type result: exec_result.ExecResult
            :type stop: threading.Event
            """
            while not stop.isSet():
                time.sleep(0.1)
                poll_streams(
                    result=result,
                    stdout=self.__process.stdout,
                    stderr=self.__process.stderr,
                )

                self.__process.poll()

                if self.__process.returncode is not None:
                    result.read_stdout(
                        src=self.__process.stdout,
                        log=logger,
                        verbose=verbose
                    )
                    result.read_stderr(
                        src=self.__process.stderr,
                        log=logger,
                        verbose=verbose
                    )
                    result.exit_code = self.__process.returncode

                    stop.set()

        # 1 Command per run
        with self.lock:
            result = exec_result.ExecResult(cmd=command)
            stop_event = threading.Event()
            message = _log_templates.CMD_EXEC.format(cmd=command.rstrip())
            if verbose:
                logger.info(message)
            else:
                logger.debug(message)
            # Run
            self.__process = subprocess.Popen(
                args=[command],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True, cwd=cwd, env=env,
                universal_newlines=False,
            )

            # Poll output
            # pylint: disable=assignment-from-no-return
            poll_thread = poll_pipes(
                result,
                stop_event
            )  # type: threading.Thread
            # pylint: enable=assignment-from-no-return
            # wait for process close
            stop_event.wait(timeout)

            # Process closed?
            if stop_event.isSet():
                stop_event.clear()
                self.__process = None
                return result
            # Kill not ended process and wait for close
            try:
                self.__process.kill()  # kill -9
                stop_event.wait(5)
                poll_thread.join(5)
            except OSError:
                # Nothing to kill
                logger.warning(
                    u"{!s} has been completed just after timeout: "
                    "please validate timeout.".format(command))
            self.__process = None

            wait_err_msg = _log_templates.CMD_WAIT_ERROR.format(
                result=result,
                timeout=timeout
            )
            logger.debug(wait_err_msg)
            raise exceptions.ExecHelperTimeoutError(wait_err_msg)

    def execute(
        self,
        command,  # type: str
        verbose=False,  # type: bool
        timeout=None,  # type: typing.Optional[int]
        **kwargs
    ):  # type: (...) -> exec_result.ExecResult
        """Execute command and wait for return code.

        Timeout limitation: read tick is 100 ms.

        :type command: str
        :type verbose: bool
        :type timeout: typing.Optional[int]
        :rtype: ExecResult
        :raises: ExecHelperTimeoutError
        """
        result = self.__exec_command(command=command, timeout=timeout,
                                     verbose=verbose, **kwargs)
        message = _log_templates.CMD_RESULT.format(result=result)
        logger.log(
            level=logging.INFO if verbose else logging.DEBUG,
            msg=message
        )

        return result

    def check_call(
        self,
        command,  # type: str
        verbose=False,  # type: bool
        timeout=None,  # type: typing.Optional[int]
        error_info=None,  # type: typing.Optional[str]
        expected=None,  # type: _type_expected
        raise_on_err=True,  # type: bool
        **kwargs
    ):  # type: (...) -> exec_result.ExecResult
        """Execute command and check for return code.

        Timeout limitation: read tick is 100 ms.

        :type command: str
        :type verbose: bool
        :type timeout: typing.Optional[int]
        :type error_info: typing.Optional[str]
        :type expected: typing.Optional[typing.Iterable[_type_exit_codes]]
        :type raise_on_err: bool
        :rtype: ExecResult
        :raises: DevopsCalledProcessError
        """
        expected = proc_enums.exit_codes_to_enums(expected)
        ret = self.execute(command, verbose, timeout, **kwargs)
        if ret['exit_code'] not in expected:
            message = (
                _log_templates.CMD_UNEXPECTED_EXIT_CODE.format(
                    append=error_info + '\n' if error_info else '',
                    result=ret,
                    expected=expected
                ))
            logger.error(message)
            if raise_on_err:
                raise exceptions.CalledProcessError(
                    result=ret,
                    expected=expected,
                )
        return ret

    def check_stderr(
        self,
        command,  # type: str
        verbose=False,  # type: bool
        timeout=None,  # type: typing.Optional[int]
        error_info=None,  # type: typing.Optional[str]
        raise_on_err=True,  # type: bool
        **kwargs
    ):  # type: (...) -> exec_result.ExecResult
        """Execute command expecting return code 0 and empty STDERR.

        Timeout limitation: read tick is 100 ms.

        :type command: str
        :type verbose: bool
        :type timeout: typing.Optional[int]
        :type error_info: typing.Optional[str]
        :type raise_on_err: bool
        :rtype: ExecResult
        :raises: DevopsCalledProcessError
        """
        ret = self.check_call(
            command, verbose, timeout=timeout,
            error_info=error_info, raise_on_err=raise_on_err, **kwargs)
        if ret['stderr']:
            message = (
                _log_templates.CMD_UNEXPECTED_STDERR.format(
                    append=error_info + '\n' if error_info else '',
                    result=ret,
                ))
            logger.error(message)
            if raise_on_err:
                raise exceptions.CalledProcessError(
                    result=ret,
                    expected=kwargs.get('expected'),
                )
        return ret
