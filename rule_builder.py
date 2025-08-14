import tkinter as tk
from tkinter import ttk, messagebox
import json

# Predefined field, operator, and actions for this demo:
CONDITION_FIELDS = ["From", "Subject", "Date received"]
STRING_OPERATORS = ["contains", "does not contain", "equals", "does not equal"]
DATE_OPERATORS = ["is less than", "is greater than"]

ACTION_TYPES = ["Move Message", "Mark as Read", "Mark as Unread"]

MAILBOXES = ["Inbox", "Sent", "Spam", "Trash"]

class ConditionRow:
    def __init__(self, parent, row, remove_callback):
        self.parent = parent
        self.row = row
        self.remove_callback = remove_callback

        self.field_var = tk.StringVar(value=CONDITION_FIELDS[0])
        self.op_var = tk.StringVar(value=STRING_OPERATORS[0])
        self.val_var = tk.StringVar()

        self.field_cb = ttk.Combobox(parent, values=CONDITION_FIELDS, width=15,
                                     textvariable=self.field_var, state="readonly")
        self.op_cb = ttk.Combobox(parent, width=20, textvariable=self.op_var, state="readonly")
        self.val_entry = tk.Entry(parent, width=22, textvariable=self.val_var)

        self.minus_btn = ttk.Button(parent, text="−", width=2, command=self.remove_row)
        self.plus_btn = ttk.Button(parent, text="+", width=2, command=self.add_row)

        self.field_cb.grid(row=row, column=0, padx=2, pady=2)
        self.op_cb.grid(row=row, column=1, padx=2, pady=2)
        self.val_entry.grid(row=row, column=2, padx=2, pady=2)
        self.minus_btn.grid(row=row, column=3, padx=2)
        self.plus_btn.grid(row=row, column=4, padx=2)

        self.field_cb.bind("<<ComboboxSelected>>", self._update_operators)
        self._update_operators()

    def _update_operators(self, event=None):
        field = self.field_var.get()
        ops = DATE_OPERATORS if field == "Date received" else STRING_OPERATORS
        self.op_cb['values'] = ops
        self.op_var.set(ops[0])

    def get(self):
        return {
            "field": self.field_var.get(),
            "operator": self.op_var.get(),
            "value": self.val_var.get()
        }

    def remove_row(self):
        self.destroy()
        self.remove_callback(self)

    def add_row(self):
        self.parent.master.add_condition_row(self.row + 1)

    def grid(self, row):
        self.field_cb.grid(row=row, column=0)
        self.op_cb.grid(row=row, column=1)
        self.val_entry.grid(row=row, column=2)
        self.minus_btn.grid(row=row, column=3)
        self.plus_btn.grid(row=row, column=4)

    def destroy(self):
        self.field_cb.destroy()
        self.op_cb.destroy()
        self.val_entry.destroy()
        self.minus_btn.destroy()
        self.plus_btn.destroy()


class ActionRow:
    def __init__(self, parent, row, remove_callback):
        self.parent = parent
        self.row = row
        self.remove_callback = remove_callback

        self.action_type = tk.StringVar(value=ACTION_TYPES[0])
        self.mailbox_var = tk.StringVar(value=MAILBOXES[0])

        self.action_cb = ttk.Combobox(parent, values=ACTION_TYPES, textvariable=self.action_type,
                                      width=16, state="readonly")
        self.mailbox_cb = ttk.Combobox(parent, values=MAILBOXES, textvariable=self.mailbox_var,
                                       width=13, state="readonly")
        self.minus_btn = ttk.Button(parent, text="−", width=2, command=self.remove_row)
        self.plus_btn = ttk.Button(parent, text="+", width=2, command=self.add_row)

        self.action_cb.grid(row=row, column=0, padx=2, pady=2)
        self.mailbox_cb.grid(row=row, column=2, padx=2, pady=2)
        self.minus_btn.grid(row=row, column=3, padx=2)
        self.plus_btn.grid(row=row, column=4, padx=2)

        self.action_cb.bind("<<ComboboxSelected>>", self.update_fields)
        self.update_fields()

    def update_fields(self, event=None):
        if self.action_type.get() == "Move Message":
            self.mailbox_cb.grid(row=self.row, column=2)
        else:
            self.mailbox_cb.grid_remove()

    def get(self):
        act = self.action_type.get()
        if act == "Move Message":
            return {"action": act, "mailbox": self.mailbox_var.get()}
        else:
            return {"action": act}

    def remove_row(self):
        self.destroy()
        self.remove_callback(self)

    def add_row(self):
        self.parent.master.add_action_row(self.row + 1)

    def grid(self, row):
        self.row = row
        self.action_cb.grid(row=row, column=0)
        if self.action_type.get() == "Move Message":
            self.mailbox_cb.grid(row=row, column=2)
        self.minus_btn.grid(row=row, column=3)
        self.plus_btn.grid(row=row, column=4)

    def destroy(self):
        self.action_cb.destroy()
        self.mailbox_cb.destroy()
        self.minus_btn.destroy()
        self.plus_btn.destroy()


class RuleApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Rule Editor")
        self.geometry("650x420")
        self.resizable(False, False)

        # ---- Description
        tk.Label(self, text="Description:").place(x=20, y=18)
        self.desc_entry = tk.Entry(self, width=50)
        self.desc_entry.place(x=114, y=18)

        # ---- IF section
        y_base = 52
        tk.Label(self, text="If ").place(x=24, y=y_base)
        self.match_var = tk.StringVar(value="all")
        ttk.Combobox(self, values=["all", "any"], textvariable=self.match_var,
                     width=6, state="readonly").place(x=45, y=y_base)
        tk.Label(self, text=" of the following conditions are met:").place(x=115, y=y_base)

        cond_frame = tk.Frame(self)
        cond_frame.place(x=24, y=y_base+26)
        self.cond_frame = cond_frame

        self.condition_rows = []
        self.add_condition_row(0, field="From", op="contains", val="tenmiles.com")
        self.add_condition_row(1, field="Subject", op="contains", val="Interview")
        self.add_condition_row(2, field="Date received", op="is less than", val="2")

        # ---- THEN/ACTION section
        y_act = y_base + 120
        tk.Label(self, text="Perform the following actions:").place(x=24, y=y_act)

        action_frame = tk.Frame(self)
        action_frame.place(x=24, y=y_act+25)
        self.action_frame = action_frame
        self.action_rows = []
        self.add_action_row(0, act="Move Message", mailbox="Inbox")
        self.add_action_row(1, act="Mark as Read")

        # ---- Buttons
        self.ok_btn = ttk.Button(self, text="OK", command=self.save_rule)
        self.ok_btn.place(x=510, y=365)
        self.cancel_btn = ttk.Button(self, text="Cancel", command=self.destroy)
        self.cancel_btn.place(x=570, y=365)

    def add_condition_row(self, index, field=None, op=None, val=None):
        cond = ConditionRow(self.cond_frame, index, self.remove_condition_row)
        if field: cond.field_var.set(field)
        if op: cond.op_var.set(op)
        if val: cond.val_var.set(val)
        self.condition_rows.insert(index, cond)
        self.refresh_conditions()

    def remove_condition_row(self, cond_row):
        self.condition_rows.remove(cond_row)
        self.refresh_conditions()

    def refresh_conditions(self):
        for idx, cond in enumerate(self.condition_rows):
            cond.grid(idx)

    def add_action_row(self, index, act=None, mailbox=None):
        act_row = ActionRow(self.action_frame, index, self.remove_action_row)
        if act: act_row.action_type.set(act)
        if mailbox: act_row.mailbox_var.set(mailbox)
        self.action_rows.insert(index, act_row)
        self.refresh_actions()

    def remove_action_row(self, act_row):
        self.action_rows.remove(act_row)
        self.refresh_actions()

    def refresh_actions(self):
        for idx, act in enumerate(self.action_rows):
            act.grid(idx)

    def save_rule(self):
        if not self.condition_rows:
            messagebox.showerror("Error", "At least one condition is required.")
            return

        rule = {
            "description": self.desc_entry.get().strip(),
            "predicate": self.match_var.get(),
            "conditions": [r.get() for r in self.condition_rows],
            "actions": [a.get() for a in self.action_rows],
        }

        try:
            with open("rules.json", "r") as f:
                rules = json.load(f)
        except FileNotFoundError:
            rules = []

        rules.append(rule)

        with open("rules.json", "w") as f:
            json.dump(rules, f, indent=4)

        messagebox.showinfo("Saved", "Rule added to rules.json")
        self.destroy()


if __name__ == "__main__":
    app = RuleApp()
    app.mainloop()