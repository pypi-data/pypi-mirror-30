from collections import UserList


__all__ = ('apps', 'AppStack')


class AppStack(UserList):
    """ A stack-like list. Calling it returns the head of the stack. """
    # ©2014, Marcel Hellkamp
    def __call__(self):
        """ Return the current default application. """
        return self[-1]

    def push(self, value=None):
        self.append(value)
        return value


apps = AppStack()
