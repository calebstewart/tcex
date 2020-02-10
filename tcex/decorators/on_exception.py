# -*- coding: utf-8 -*-
"""App Decorators Module."""


class OnException:
    """Set exit message on failed execution.

    This decorator will catch the generic "Exception" error, log the supplied error message, set
    the "exit_message", and exit the App with an exit code of 1.

    .. code-block:: python
        :linenos:
        :lineno-start: 1

        @OnException(exit_msg='Failed to process JSON data.')
        def my_method(json_data):
            json.dumps(json_data)

    Args:
        exit_msg (str): The message to send to exit method.
        exit_enabled (boolean|str, kwargs): Accepts a boolean or string value.  If a boolean value
            is provided that value will control enabling/disabling this feature. A string
            value should reference an item in the args namespace which resolves to a boolean.
            The value of this boolean will control enabling/disabling this feature.
        write_output (boolean): default True.
            If enabled, will call app.write_output() when an exception is raised.
    """

    def __init__(self, exit_msg=None, exit_enabled=True, write_output=True):
        """Initialize Class properties"""
        self.exit_enabled = exit_enabled
        self.exit_msg = exit_msg or 'An exception has been caught. See the logs for more details.'
        self.write_output = write_output

    def __call__(self, fn):
        """Implement __call__ function for decorator.

        Args:
            fn (function): The decorated function.

        Returns:
            function: The custom decorator function.
        """

        def exception(app, *args, **kwargs):
            """Call the function and handle any exception.

            Args:
                app (class): The instance of the App class "self".
            """
            # self.enable (e.g., True or 'fail_on_false') enables/disables this feature
            enabled = self.exit_enabled
            if not isinstance(self.exit_enabled, bool):
                enabled = getattr(app.args, self.exit_enabled)
                if not isinstance(enabled, bool):  # pragma: no cover
                    raise RuntimeError(
                        'The exit_enabled value must be a boolean or resolved to bool.'
                    )
            app.tcex.log.debug(f'Fail enabled is {enabled} ({self.exit_enabled}).')

            try:
                return fn(app, *args, **kwargs)
            except Exception as e:
                app.tcex.log.error(f'method failure ({e})')
                app.exit_message = self.exit_msg
                if self.write_output:
                    app.tcex.playbook.write_output()
                    if hasattr(app, 'write_output'):
                        app.write_output()
                if enabled:
                    app.exit_message = self.exit_msg  # for test cases
                    app.tcex.exit(1, self.exit_msg)

        return exception
