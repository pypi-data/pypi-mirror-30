# tkpane.py
#
# PURPOSE
#   Simplify the construction of a Tkinter UI by encapsulating one or more
#   widgets into 'pane' objects that have no direct dependence on any other
#   UI elements.  Panes interact with other application elements through
#   methods and callback functions.
#
# AUTHORS
#   Dreas Nielsen (RDN)
#   Elizabeth Shea (ES)
#
# COPYRIGHT AND LICENSE
#   Copyright (c) 2018, R. Dreas Nielsen
#   This program is free software: you can redistribute it and/or modify it 
#   under the terms of the GNU General Public License as published by the Free 
#   Software Foundation, either version 3 of the License, or (at your option) 
#   any later version. This program is distributed in the hope that it will be 
#   useful, but WITHOUT ANY WARRANTY; without even the implied warranty of 
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General 
#   Public License for more details. The GNU General Public License is available 
#   at http://www.gnu.org/licenses/.
#
#===============================================================================

"""Encapsulate UI elements in a 'pane' object with uniform methods for enabling, 
disabling, and clearing the contained widgets; standard lists of callback methods 
that pass specific data to allow communication between panes, and callback methods
for reporting status and progress."""

__version__ = "1.0.0"


try:
    import Tkinter as tk
except:
    import tkinter as tk
try:
    import ttk
except:
    from tkinter import ttk

import copy


#===============================================================================
#       Configuration variables
#-------------------------------------------------------------------------------

# 'invalid_color' will be used as the background color of Entry or other
# widgets when the data value is invalid.  These colors will be used as the
# default by new TkPane subclass objects when they are instantiated.  The
# colors for any pane subclass can be overridded using the 'set_invalid_color()
# method.  Tkinter (tk) and ttk widgets respond differently to these settings
# when using the default themes on Linux and Windows.
invalid_color = "#fff5ff"
invalid_disabled_color = "#ece7ec"
valid_color = "#ffffff"

# Determine whether panes defined in tkpane.lib use ttk widgets if they exist
# (the default), or Tkinter widgets.
use_ttk = True




#===============================================================================
#       Action method handlers
# Handler objects are to be used in the action method callbacks of the TkPane class.
#-------------------------------------------------------------------------------

class CbHandler(object):
    """Define a callback function that takes no arguments."""
    
    def __init__(self, function):
        self.function = function

    def call(self, tkpane_obj):
        # This method takes a TkPane object for consistency with other Handler
        # classes, although the TkPane object is not used.
        self.function()


class PaneDataHandler(CbHandler):
    """Define a callback function that will receive a dictionary of a pane's own data values."""
    
    def call(self, tkpane_obj):
        self.function(tkpane_obj.values())


class PaneKeyHandler(CbHandler):
    """Define a callback function that will receive a list of a pane's own data keys."""

    def call(self, tkpane_obj):
        self.function(tkpane_obj.datakeylist)


class AllDataHandler(CbHandler):
    """Define a callback function that will receive a dictionary of all of a pane's data values."""

    def call(self, tkpane_obj):
        self.function(tkpane_obj.datadict)


class PaneAllDataHandler(CbHandler):
    """Define a callback function that will receive the calling pane object and a dictionary of all of that pane's data values."""

    def call(self, tkpane_obj):
        self.function(tkpane_obj, tkpane_obj.datadict)



def has_handler_function(handler_list, function):
    """Determine whether any Handler object in the given list is for the specified function.
    
    Returns True or False.
    """
    for h in handler_list:
        if h.function == function:
            return True
    return False



#===============================================================================
#       The TkPane class
#-------------------------------------------------------------------------------

class TkPane(tk.Frame):
    """Base class for Tkinter UI elements (panes).  This class is meant to be subclassed,

    Subclasses are expected to call the TkPane class' initialization function.
    
    :param parent: The parent widget for this pane (ordinarily a frame or top-level element).
    :param config_opts: A dictionary of keyword arguments for configuring the pane's frame.
    :param grid_opts: A dictionary of keyword arguments for gridding the pane's frame.
    
    Attributes of a TkPane object that may be assigned after instantiation are:
    
    * required: A Boolean indicating whether valid data must be entered.
      Note that this applies to all widgets on the pane.  If some data values
      are required by the application and others are not, the widgets for
      those different data values should be on different panes.
    * datakeylist: A list of dictionary keys for data items managed by this
      pane.
    * datadict: A dictionary containing all data managed or used by this pane.
    * on_change_data_valid: A list of CbHandler object to be called when data
      are changed and valid.
    * on_change_data_invalid: A list of CbHandler objects to be called when
      data are changed and invalid.
    * on_exit_data_valid: A list of CbHandler objects to be called when the
      pane loses focus and the data are valid.
    * on_exit_data_invalid: A list of CbHandler objects to be called when
      the pane loses focus and the data are invalid.
    * on_save_change: A list of CbHandler objects to be called when the
      values of the pane's own data keys are modified in the pane's internal 
      data dictionary.
    * on_enable: A list of CbHandler objects to be called when this pane
      is enabled.
    * on_clear: A list of CbHandler objects to be called when this pane
      is cleared.
    * on_disable: A list of CbHandler objects to be called when this pane
      is disabled.
    * keys_to_enable: Keys of datadict that must be defined for this pane
      to be enabled.
    * data_to_enable: A dictionary of data values that are required for this
      pane to be enabled.  The keys of this dictionary are keys of self.datadict
      and the value for each key is a list of allowable values for that key.
    * status_reporter: An object with a well-known method (set_status)
      for reporting status information.
    * progress_reporter: An object with well-known methods (set_determinate,
      set_indeterminate, set_value, start, stop) for reporting or displaying
      progress information.
    
    Methods to be overridden by subclasses that manage data are:
    
    * save_data(is_valid): Updates or clears the data dictionary with widget values, depending on whether the data are valid.
    * valid_data(widget=None): Evaluates whether data entered into widgets on the pane are valid, Returns True or False.
    * entry_widgets(): Returns a list of widgets used for data entry.
    * enable_pane(): Enable widgets on this pane.
    * clear_pane(): Clear data from widgets on this pane.
    * disable_pane(): Disable widgets on this pane.
    
    Other methods that may commonly be overridden by subclasses are:
    
    * focus
    * set_data
    
    Subclasses must create all the widgets on the pane and configure their
    appearance and actions.  Interactions between panes should be managed
    using the lists of CbHandler callbacks.
    """

    def __init__(self, parent, pane_name, config_opts=None, grid_opts=None):
        # Create and configure the Frame for this pane.
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.pane_name = pane_name
        if config_opts is not None:
            self.configure(**config_opts)
        self.original_values = {}
        self.widget_type = None
        self.grid(row=0, column=0, sticky=tk.NSEW)
        if grid_opts is not None:
            self.grid(**grid_opts)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        # When the user enters the pane, copy the datadict for later comparison.
        self.bind("<Enter>", self.entering)
        # When the user leaves the pane, trigger a method to update the datadict,
        # cascade CbHandler functions, and send a status message.
        self.bind("<Leave>", self.leaving)
        self.bind("<FocusOut>", self.leaving)
        # 'invalid_color' will be used as the background color of Entry or other
        # widgets when the data value is invalid.  If 'invalid_color' is assigned
        # directly, it will not be applied immediately; use 'set_invalid_color()'
        # to assign *and* apply it.
        self.invalid_color = invalid_color
        self.invalid_disabled_color = invalid_disabled_color
        self.valid_color = valid_color
        #=======================================================================
        #       ASSIGNABLE CALLBACKS
        # Callback function handlers (PaneDataHandler, PaneKeyHandler, or
        # AllDataHandler objects) should be assigned to each of these lists
        # as appropriate.
        #-----------------------------------------------------------------------
        # Handlers that will be called when data in the pane are changed during
        # editing (e.g., during key entry into an Entry widget) and the data
        # are valid.  These handlers might enable other panes.
        self.on_change_data_valid = []
        # Handlers that will be called when data in the pane are changed during
        # editing (e.g., during key entry into an Entry widget) and the data
        # are invalid.  These handlers might disable and/or clear other panes.
        self.on_change_data_invalid = []
        # Handlers that will be called when the pane loses focus and the data
        # are valid.
        self.on_exit_data_valid = []
        # Handlers that will be called when the pane loses focus and the data
        # are invalid.
        self.on_exit_data_invalid = []
        # Handlers that will be called when this pane is enabled.
        self.on_enable = []
        # Handlers that will be called when this pane is cleared.
        self.on_clear = []
        # Handlers that will be called when this pane is disabled.
        self.on_disable = []
        # Handlers that will be called if the pane's own data key values in the
        # data dictionary are changed.
        self.on_save_change = []
        #=======================================================================
        #       ASSIGNABLE ATTRIBUTES
        # The following attributes should be assigned, as needed, after
        # a TkPane subclass object is instantiated.
        #-----------------------------------------------------------------------
        # The 'required' Boolean should be used to control whether widget data
        # are valid if missing.  This will require customization of the subclass 
        # by binding the <FocusOut> event to input widgets using a method that 
        # implements the validity check.
        self.required = False
        # 'datakeylist' should contain the names (keys) of only the data items 
        # managed by this pane.
        self.datakeylist = []
        # 'datadict' contains values of data items managed by this pane and also, 
        # possibly, other data values (e.g., as provided by calls to 'enable()') 
        # that may be needed.
        self.datadict = {}
        # 'keys_to_enable' should contain a list of the datadict keys that must be
        # defined for the pane to actually enable itself.  This may include some,
        # all, or none of the values in 'datakeylist', and may include other
        # data keys such as those provided to the 'enable' method or to some
        # custom method.
        self.keys_to_enable = []
        # 'data_to_enable' is a dictionary of data values with keys that should
        # be in self.datadict, where each value in 'data_to_enable' is a list
        # of allowable data values for that key in self.datadict.
        self.data_to_enable = {}
        # 'status_reporter' should be an object with well-known methods for
        # reporting textual status information, as on a status bar.  Method
        # names should be:
        #    * 'set_status': Displays the specified text.
        #    * 'clear_status': Clears any displayed text.
        self.status_reporter = None
        # 'progress_reporter' should be an object with well-known methods for
        # reporting progress, as on a progress bar.  Method names should be:
        #    * 'set_determinate': Sets a progress bar to show progress over a 
        #      fixed range of values, e.g., 0 to 100.
        #    * 'set_indeterminate': Sets a progress bar to show a continuously
        #      active progress indicator (e.g., oscillating).
        #    * 'set_value': Sets a definite progress bar to a specific value.
        #    * 'start': Starts an indefinite progress bar.
        #    * 'stop': Stops an indefinite progress bar.
        self.progress_reporter = None
        #=======================================================================

    def call_handlers(self, handler_list):
        for h in handler_list:
            h.call(self)

    def save_data(self, is_valid, entry_widget=None):
        """Update the pane's data dictionary with data from entry widgets.
        
        This may add a value, revise a value, or remove a key (if not is_valid).
        This may also change widget displays, e.g., setting invalid values to
        empty strings or the equivalent.
        
        This method ordinarily should be overridden by any subclass that manages data.
        """
        pass

    def valid_data(self, entry_widget=None):
        """Evaluate whether data entered into one or all widgets on the pane are valid,
        
        Returns True or False.  Defaults to returning True.
        This method must be overridden by any subclass that manages data.
        """
        return True
    
    def show_widget_validity(self, widget, is_valid):
        """Set the widget's background color to the 'valid' or 'invalid' color.
        
        tk and ttk widgets are handled differently.  This implementation assumes
        that Text, Listbox, and Spinbox widgets are all tk widgets, and all others
        are ttk widgets (as in tkpane.lib).  If other types of widgets
        are used (e.g., a tk.Entry widget), this method will have to be overridden.
        """
        if self.invalid_color is not None:
            wclass = widget.winfo_class()
            if self.widget_type is not None:
                wtype = self.widget_type
            else:
                wtype = "tk" if wclass in ("Text", "Listbox", "Spinbox") else "ttk"
            if wtype == "tk":
                # tk widgets.
                col = self.valid_color if is_valid or not self.required else self.invalid_color
                try:
                    widget.configure(background=col)
                except:
                    pass
            else:
                # ttk widgets.
                try:
                    sname = widget["style"] or wclass
                    disabled_color = ttk.Style().lookup(sname, 'fieldbackground', ('disabled',))
                    ttk.Style().map(sname,
                        fieldbackground=[(['invalid','!disabled'], self.invalid_color),
                                        (['invalid','disabled'], self.invalid_disabled_color),
                                        (['!invalid', 'disabled'], disabled_color)])
                    vstate = '!invalid' if is_valid else 'invalid'
                    st = list(widget.state())
                    if 'invalid' in st:
                        st.remove('invalid')
                    if '!invalid' in st:
                        st.remove('!invalid')
                    st.append(vstate)
                    widget.state(st)
                except:
                    pass
    
    def entry_widgets(self):
        """Return a list of entry widgets on the pane.
        
        The purpose of this method is for the TkPane to automatically recolor
        all entry widgets based on their validity.  Defaults to returning an
        empty list.
        
        This method should be overridden by any subclass that manages data.
        """
        return []
    
    def show_widgets_validity(self):
        """Set all widgets' background color to the 'valid' or 'invalid' color."""
        for w in self.entry_widgets():
            self.show_widget_validity(w, self.valid_data(w))
    
    def handle_change_validity(self, is_valid, entry_widget=None):
        """Update the data dictionary from pane widgets and call appropriate handlers for data changes.
        
        :param is_valid: A Boolean indicating whether or not data on the pane are valid.
        :param entry_widget: The widget that has been changed.  Its state will be changed as appropriate to indicate the data validity.
        
        If entry_widget is not provided, all widgets will have their state changed to indicate the data validity.
        """
        prior_values = copy.deepcopy(self.datadict)
        self.save_data(is_valid, entry_widget)
        if self.datadict != prior_values:
            self.call_handlers(self.on_save_change)
        if is_valid:
            self.call_handlers(self.on_change_data_valid)
        else:
            self.call_handlers(self.on_change_data_invalid)
        if entry_widget is not None:
            self.show_widget_validity(entry_widget, is_valid)
        else:
            for w in self.entry_widgets():
                self.show_widget_validity(w, is_valid)
    
    def handle_exit_validity(self, is_valid, widget_list=None):
        """Update the data dictionary from pane widgets and call appropriate handlers for pane exiting.
        
        :param is_valid: A Boolean indicating whether or not data on the pane are valid.
        :param widget_list: A list of widgets to which 'is_valid' applies.  Their states will be changed as appropriate to indicate the data validity.
        
        If widget_list is not provided, all widgets will have their state changed to indicate the data validity.
        """
        prior_values = copy.deepcopy(self.datadict)
        self.save_data(is_valid, None)
        if self.datadict != prior_values:
            self.call_handlers(self.on_save_change)
        if is_valid:
            self.call_handlers(self.on_exit_data_valid)
        else:
            self.call_handlers(self.on_exit_data_invalid)
        if widget_list is not None:
            for w in widget_list:
                self.show_widget_validity(w, is_valid)
        else:
            for w in self.entry_widgets():
                self.show_widget_validity(w, is_valid)
    
    def send_status_message(self, is_valid):
        """Send a status message reporting data values and/or validity if data have changed.
        
        :param is_valid: A Boolean indicating whether or not the data on the pane are valid.
        
        This method may be overridden."""
        if self.datadict != self.original_values:
            if is_valid:
                vals = self.values()
                dk = list(vals.keys())
                if len(dk) == 0:
                    self.report_status(u"%s data cleared." % self.pane_name)
                elif len(dk) == 1:
                    self.report_status(u"%s set to %s." % (self.pane_name, vals[dk[0]]))
                else:
                    msg = "%s data set to:" % self.pane_name
                    for i, k in enumerate(dk):
                        if i > 0:
                            msg += ";"
                        msg += "%s %s=%s" % (msg, k, vals[k])
                    msg += "."
                    self.report_status(msg)
            else:
                self.report_status(u"%s is invalid." % self.pane_name)

    def entering(self, event):
        """Record the initial data value to be used later to determine if it has changed."""
        self.original_values = copy.deepcopy(self.datadict)
    
    def leaving(self, event):
        """Revise the data dictionary, call all exit handlers, and report status.
        
        Revision of the data dictionary is carried out through the save_data
        method, which should be overridden by subclasses.  The appropriate set
        of exit handlers is called depending on sata validity.
        """
        is_valid = self.valid_data(None)
        self.handle_exit_validity(is_valid)
        self.send_status_message(is_valid)
        if is_valid and self.original_values != self.datadict:
            self.original_values = copy.deepcopy(self.datadict)

    def values(self):
        """Return data values managed by this pane as a dictionary.

        If the 'datakeylist' and 'datadict' attributes are managed properly,
        this function will work as intended, but subclasses may need to
        override this method if they are not using the datadict to store the
        pane's data.
        """
        return dict([(k, self.datadict[k]) for k in self.datakeylist if k in self.datadict])
    
    def all_data(self):
        """Return all data in this pane's data dictionary, as a dictionary."""
        return self.datadict
    
    def set_invalid_color(self, invalid_color, invalid_disabled_color):
        """Save the colors to be applied to any invalid widgets, and immediately apply them."""
        self.invalid_color = invalid_color
        self.invalid_disabled_color = invalid_disabled_color
        self.show_widgets_validity()

    def requires(self, other_pane, enable_on_other_exit_only=False, disable_on_other_exit_only=False, clear_on_enable=False, clear_on_disable=False):
        """Set handler functions for the other pane to enable or disable this pane.
        
        :param other_pane: The pane which must have valid data for this pane to be enabled.
        :param enable_on_other_exit_only: A Boolean indicating whether this pane should be enabled only when the other pane exits with valid data (True) or any time the other pane's data become valid (False).  Default: False.
        :param disable_on_other_exit_only: A Boolean indicating whether this pane should be disabled only when the other pane exits with invalid data (True) or any time the other pane's data become invalid (False).  Default: False.
        :param clear_on_enable: A Boolean indicating whether this pane should be cleared when it is enabled.  Default: False.
        :param clear_on_disable: A Boolean indicating whether this pane should be cleared when it is disabled.  Default: False.
       
        The other pane's lists of CbHandler callbacks are modified to enable or
        disable this pane when the other pane's data are valid or invalid,
        respectively.  This pane's 'clear-data()' method is also added to the other
        pane's 'on_clear' callback list.  The other pane's 'required' attribute 
        is also set to True.  Optionally, this pane can also be cleared when it 
        is either enabled or disabled as a result of data validity changes in the
        other pane.
        """
        other_pane.required = True
        self.keys_to_enable = list(set(self.keys_to_enable) | set(other_pane.datakeylist))
        if not enable_on_other_exit_only:
            if not has_handler_function(other_pane.on_change_data_valid, self.enable):
                other_pane.on_change_data_valid.append(PaneDataHandler(self.enable))
        if not has_handler_function(other_pane.on_exit_data_valid, self.enable):
            other_pane.on_exit_data_valid.append(PaneDataHandler(self.enable))
        if not disable_on_other_exit_only:
            if not has_handler_function(other_pane.on_change_data_invalid, self.disable):
                other_pane.on_change_data_invalid.append(PaneKeyHandler(self.disable))
        if not has_handler_function(other_pane.on_exit_data_invalid, self.disable):
            other_pane.on_exit_data_invalid.append(PaneKeyHandler(self.disable))
        if not has_handler_function(other_pane.on_clear, self.clear_data):
            other_pane.on_clear.append(PaneKeyHandler(self.clear_data))
        if clear_on_enable:
            if not has_handler_function(other_pane.on_enable, self.clear):
                other_pane.on_enable.append(PaneKeyHandler(self.clear))
        if clear_on_disable:
            if not has_handler_function(other_pane.on_disable, self.clear):
                other_pane.on_disable.append(PaneKeyHandler(self.clear))
        other_pane.show_widgets_validity()

    def requires_datavalue(self, key, value):
        """Specify that a particular data value, for a specific data key, is required for the pane to enable itself.
        
        :param key: The key for the data value, that must be in the pane's data dictionary.
        :param value: The value, or list of values, that must be in the pane's data dictionary for that key.
        
        This method does not create any callbacks that cause the other pane that
        provides the data value to enable or disable the current pane.  When the
        ``requires_datavalue()`` method is used, it may be appropriate to also use
        the ``requires()`` method, specifying the other pane that provides those data values.
        """
        valuelist = list((value,)) if not isinstance(value, list) else value
        self.data_to_enable[key] = list(set(self.data_to_enable.get(key, [])) or set(valuelist))

    def can_use(self, other_pane):
        """Set handler functions so that the other pane can provide data for the data dictionary, or keys of data to remove.
        
        :param other_pane: The pane which must have valid data for this pane to be enabled.
       
        The other pane's lists of Handler callbacks are modified to add the other
        pane's data to this pane's data dictionary or to clear the other pane's data 
        keys from this pane's data dictionary when the other pane's data are valid or 
        invalid, respectively.
        """
        if not has_handler_function(other_pane.on_change_data_valid, self.use_data):
            other_pane.on_change_data_valid.append(PaneDataHandler(self.use_data))
        if not has_handler_function(other_pane.on_exit_data_valid, self.use_data):
            other_pane.on_exit_data_valid.append(PaneDataHandler(self.use_data))
        if not has_handler_function(other_pane.on_change_data_invalid, self.clear_data):
            other_pane.on_change_data_invalid.append(PaneKeyHandler(self.clear_data))
        if not has_handler_function(other_pane.on_exit_data_invalid, self.clear_data):
            other_pane.on_exit_data_invalid.append(PaneKeyHandler(self.clear_data))
        if not has_handler_function(other_pane.on_clear, self.clear_data):
            other_pane.on_clear.append(PaneKeyHandler(self.clear_data))

    def clear_on_disable(self):
        """Clears the pane's own data and pane (widgets) when the pane is disabled."""
        if not has_handler_function(self.on_disable, self.clear):
            self.on_disable.append(PaneDataHandler(self.clear))

    def can_enable(self):
        """Determine whether all the required data values are available for this pane to actually enable itself.
        
        Returns True or False.
        """
        if len(self.data_to_enable) > 0:
            req_met = True
            for req_key in self.data_to_enable:
                if req_key in self.datadict:
                    dictval = self.datadict[req_key]
                    if isinstance(dictval, list):
                        req_met = any(x in self.data_to_enable[req_key] for x in dictval)
                    else:
                        req_met = dictval in self.data_to_enable[req_key]
                else:
                    req_met = False
                if not req_met:
                    break
        else:
            req_met = True
        rv = all([dk in self.datadict.keys() for dk in self.keys_to_enable]) \
            and req_met
        return rv

    def _enablewidgets(self, widgetlist):
        for w in widgetlist:
            try:
                # ttk widget
                w.state(["!disabled"])
            except:
                try:
                    # tk widget
                    w.configure(state=tk.NORMAL)
                except:
                    pass

    def enable_pane(self):
        """ Enable any widgets on this pane that are necessary for initial user interaction.

        This method should be overridden by child classes.
        This method is not meant to be called directly, but only called indirectly
        via the enable() method.
        """
        pass

    def enable(self, incoming_data={}):
        """Enable this pane (subject to data requirements being met).

        :param incoming_data: A dictionary of data from the caller.
        
        The incoming data will be merged into this pane's own data dictionary.
        """
        if incoming_data is not None:
            prev_data = self.values()
            self.datadict.update(incoming_data)
            if self.values() != prev_data:
                self.call_handlers(self.on_save_change)
        if self.can_enable():
            self.enable_pane()
            self.call_handlers(self.on_enable)
        else:
            self.disable_pane()
            self.call_handlers(self.on_disable)
    
    def __delete_data(self, keylist):
        prev_data = self.values()
        for k in keylist:
            if k in self.datadict:
                del self.datadict[k]
        if self.values() != prev_data:
            self.call_handlers(self.on_save_change)

    def clear_own(self):
        """Clears the pane's own data from its data dictionary.
        
        This is intended primarily for use by subclasses.  It does not clear
        the pane's visible data, so it can lead to inconsistencies if not
        used properly.
        """
        self.__delete_data(self.datakeylist)
        
    def clear_data(self, keylist=None):
        """Remove the values for the specified keys from the pane's data dictionary.
        
        :param data_keys: A list of keys of the dictionary entries to remove.
        
        This method removes some or all data values not managed by this pane
        from the pane's data dictionary.
        
        If any of the specified keys are for the data managed by this pane,
        then *all* of the data managed by this pane will be cleared, as well as
        any other values in keylist; the pane will be cleared; and all callbacks
        in the ``on_clear`` list will be called--that is, this method will act
        as if the ``clear()`` method had been called instead.
        
        If no data keys are specified, all data values that are *not* managed by
        this pane will be removed.
        """
       #if keylist is None:
        if not keylist:
            #self.__delete_data(keys = list(set(self.datadict.keys()) - set(self.datakeylist)))
            self.__delete_data(keylist = list(set(self.datadict.keys()) - set(self.datakeylist)))
        else:
            if any(set(keylist) & set(self.datakeylist)):
                self.clear(keylist)
            else:
                self.__delete_data(keylist)

    def clear_pane(self):
        """Clear data from widgets on this pane, as appropriate.

        This method should be overridden by child classes.
        This method is not meant to be called directly, but only called indirectly
        via the clear() method.
        """
        pass
        
    def clear(self, keylist=[]):
        """Re-initialize any data entry or display elements on the pane, and remove stored data.
        
        :param keylist: A list of keys for data to be removed from the pane's data dictionary.

        This method will remove data for the given keys from the pane's data
        dictionary, *and also* remove all of the pane's own data.  Any data 
        displayed on the pane will be cleared (subject to the subclass' 
        implementation of the `clear_pane()`` method).  All of the ``on_clear``
        callbacks will be called.
        """
        self.clear_pane()
        keys = (list(set(keylist) | set(self.datakeylist)))
        self.__delete_data(keys)
        self.call_handlers(self.on_clear)
    
    def _disablewidgets(self, widgetlist):
        for w in widgetlist:
            try:
                # ttk widget.
                w.state(["disabled"])
            except:
                try:
                    # tk widget.
                    w.configure(state=tk.DISABLED)
                except:
                    pass

    def disable_pane(self):
        """Disable any widgets on this pane that are necessary for user interaction.

        This method should be overridden by child classes.
        This method is not meant to be called directly, but only called indirectly
        via the disable() method.
        """
        pass

    def disable(self, keylist=[]):
        """Disable the pane so that the user can't interact with it.

        :param keylist: A list of the keys to be removed from the pane's data dictionary.

        This method may be overridden by child classes if simply overriding
        the disable_pane() method is not sufficient to implement the needed behavior.
        """
        self.clear_data(keylist)
        self.disable_pane()
        self.call_handlers(self.on_disable)
    
    def _setstyle(self, widgetlist, ttk_style):
        for w in widgetlist:
            try:
                w['style'] = ttk_style
            except:
                pass

    def set_style(self, ttk_style):
        """Set the style of the widget(s) on this pane.
        
        This method should be overridden by subclasses. It is part of the standard
        interface of a pane, and has no action in the base TkPane class.
        """
        pass
    
    def focus(self):
        """Set the focus of this pane to the appropriate widget.
        
        This method should be overridden by subclasses.  It is part of the standard
        interface of a pane, and has no action in the base TkPane class.
        """
        pass

    def set_data(self, data):
        """Accepts data to be used by the pane as appropriate.
        
        :param data: This is intended to be a dictionary, but subclasses that override this method can accept any number of parameters of any type.
        
        This method allows other panes or application code to send data to a pane
        without triggering any callbacks.  The use of this data and even the type
        of data may be redefined by the custom pane subclass, and should be
        respected by the caller.  No other TkPane methods use this method; it exists
        only to provide a uniform data-passing method for all subclasses.
        """
        self.datadict.update(data)
    
    def use_data(self, data):
        # A method that accepts data to be added to the pane's data dictionary.
        # This has the same function as 'set_data()', but whereas 'set_data()'
        # may be overridden by subclasses, and may assign special meaning to
        # some data keys, this method does not.  This method should not be
        # overridden because it is added to callback lists by the 'can_use()'
        # method.
        self.datadict.update(data)
    
    def set_allbut(self, data, exclude_keys):
        # A convenience function for subclasses that updates the pane's data dictionary
        # with all values from the passed dictionary 'data' except for those in the
        # 'exclude_keys' list.  This facilitates subclasses' support for special keys.
        for key in data:
            if key not in exclude_keys:
                self.datadict[key] = data[key]
        
    def report_status(self, status_msg):
        """Send the given message to the status reporting function, if it is defined."""
        if self.status_reporter is not None:
            self.status_reporter.set_status(status_msg)
    
    def report_progress(self, progress_value):
        """Send the given progress value to the progress reporting function, if it is defined."""
        if self.progress_reporter is not None:
            self.progress_reporter.set_value(progress_value)


# ==============================================================================
#       Utility functions
#-------------------------------------------------------------------------------

def run_validity_callbacks(panelist):
    """Run the 'on_exit_data_(in)valid' callbacks for all panes in the list,
    
    This function is intended to be used after all panes have been instantiated,
    when some panes have default values and are required by other panes.  This
    function will ensure that the dependent panes have the required initial data
    values.
    """
    for p in panelist:
        p.handle_exit_validity(p.valid_data())


def enable_or_disable_all(panelist):
    """Enable or disable all panes in the list, as required by their data status.
    
    This function is intended primarily to be used after the UI has been built
    but before it has been activated, to ensure that all of the specified panes
    are initallly appropriately enabled or disabled.
    """
    for p in panelist:
        if p.can_enable():
            p.enable()
        else:
            p.disable()


def en_or_dis_able_all(panelist):
    enable_or_disable_all(panelist)


class LayoutPaneGroup(dict):
    def add_element(self, element_name, element):
        # Add the pane for the given element (if any) as a dictionary item.
        fr = element.frame
        if fr is not None:
            widgets = fr.winfo_children()
            if len(widgets) == 1:
                # When there is a pane, it should be the only child of the enclosing frame.
                w = widgets[0]
                try:
                    if any(['TkPane' in str(c) for c in w.__class__.__bases__]):
                        self[element_name] = w
                except:
                    pass
    def merge(self, other):
        # Merge panes from the 'other' object (ordinarily another LayoutPaneGroup
        # object) into self.
        self.update(other)
            



def layout_panes(layout):
    """Take a tklayout.AppLayout object and return a dictionary of pane objects with AppLayout identifiers as keys,
    
    If the ``tklayout`` package has been used to assemble panes into a UI, this 
    function will create and return a dictionary of all of the AppLayout element
    names and corresponding pane objects.  This can simplify access to the pane 
    objects for subsequent customization.
    """
    
    panes = LayoutPaneGroup()
    for element_name in layout.partslist:
        panes.add_element(element_name, layout.partslist[element_name])
    return panes


def build_ui(layout_spec, tk_parent, ui_root_element, build_specs):
    """Take specifications for a UI layout and panes, and assemble them, returning a dictionary of panes.
    
    :param layout_spec: A tklayout.AppLayout object for which all of the UI elements have been described.
    :param tk_parent: The Tkinter widget (e.g., a frame) that will be the parent widget for the entire UI.
    :param ui_root_element: The name of the layout element (in 'layout_spec') that is the container for all other layout elements.
    :param build_specs: A dictionary of layout element names and functions to populate those elements with panes (as is needed by tklayout.build_elements).
    
    This is a convenience function that integrates operations of the ``tklayout``
    and ``tkpane`` packages to minimize application code.
    """
    layout_spec.create_layout(tk_parent, ui_root_element)
    layout_spec.build_elements(build_specs)
    return layout_panes(layout_spec)
