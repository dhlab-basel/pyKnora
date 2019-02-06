from typing import List, Set, Dict, Tuple, Optional
from knora import KnoraError, knora
import wx
from pprint import pprint


class KnoraConsole(wx.Frame):
    """
    Main Window for Knora console
    """

    def __init__(self, *args, **kw):
        super(KnoraConsole, self).__init__(*args, **kw)

        nb = wx.Notebook(self)

        up = UserPanel(nb)
        nb.InsertPage(index=0, page=up, text="User")


        # create a menu bar
        self.makeMenuBar()

        # and a status bar
        self.CreateStatusBar()
        self.SetStatusText("Knora Console")

    def makeMenuBar(self):
        """
        A menu bar is composed of menus, which are composed of menu items.
        This method builds a set of menus and binds handlers to be called
        when the menu item is selected.
        """

        # Make a file menu with Hello and Exit items
        fileMenu = wx.Menu()
        # The "\t..." syntax defines an accelerator key that also triggers
        # the same event
        helloItem = fileMenu.Append(-1, "&Hello...\tCtrl-H",
                                    "Help string shown in status bar for this menu item")
        fileMenu.AppendSeparator()
        # When using a stock ID we don't need to specify the menu item's
        # label
        exitItem = fileMenu.Append(wx.ID_EXIT)

        # Now a help menu for the about item
        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)

        # Make the menu bar and add the two menus to it. The '&' defines
        # that the next letter is the "mnemonic" for the menu item. On the
        # platforms that support it those letters are underlined and can be
        # triggered from the keyboard.
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(helpMenu, "&Help")

        # Give the menu bar to the frame
        self.SetMenuBar(menuBar)

        # Finally, associate a handler function with the EVT_MENU event for
        # each of the menu items. That means that when that menu item is
        # activated then the associated handler function will be called.
        self.Bind(wx.EVT_MENU, self.OnHello, helloItem)
        self.Bind(wx.EVT_MENU, self.OnExit, exitItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)

    def OnExit(self, event):
        """Close the frame, terminating the application."""
        self.Close(True)

    def OnHello(self, event):
        """Say hello to the user."""
        wx.MessageBox("Hello again from wxPython")

    def OnAbout(self, event):
        """Display an About Dialog"""
        wx.MessageBox("This is a wxPython Hello World sample",
                      "About Hello World 2",
                      wx.OK | wx.ICON_INFORMATION)


class UserPanel(wx.Panel):
    """
    User tab
    """
    def __init__(self, *args, **kw):
        super(UserPanel, self).__init__(*args, **kw)
        listctl = wx.ListCtrl(self, name="Users:", style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        listctl.AppendColumn("Username", width=wx.LIST_AUTOSIZE)
        listctl.AppendColumn("Lastname", width=wx.LIST_AUTOSIZE)
        listctl.AppendColumn("Firstname", width=wx.LIST_AUTOSIZE)
        listctl.AppendColumn("Email", width=wx.LIST_AUTOSIZE)
        users = con.get_users()
        for user in users:
            listctl.Append((user['username'], user['familyName'], user['givenName'], user['email']))
        listctl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.listclick)

    def listclick(selfself, event):
        print(event.GetEventObject().GetFirstSelected())



if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    con = knora('http://0.0.0.0:3333', 'root@example.com', 'test')

    app = wx.App()
    frm = KnoraConsole(None, title='Knora Console V0.1.1 Beta', size=wx.Size(800, 600))
    frm.Show()
    app.MainLoop()
