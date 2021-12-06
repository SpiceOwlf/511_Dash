class Action:
    def __init__(self, idx, prev=None, current=None, column=''):
        self.type = ''
        if prev is None:
            self.type = 'Insertion'
        elif current is None:
            self.type = 'Deletion'
        else:
            self.type = 'Modification'

        self.idx = idx
        self.column = column
        self.prev = prev
        self.current = current


class ColumnBasedModel:
    def __init__(self, column_names: list, records: list):
        self.column_names = column_names
        # self.column_names.insert(0, 'idx')
        self.columns = self.load(column_names, records)
        self.displayed_columns = self.load(column_names, records)
        self.displayed_column_names = list(self.displayed_columns.keys())
        self.deletion_record = []
        self.last_actions = []
        self.displayed_last_actions = []
        assert self.check_consistency()

    def load(self, column_names: list, records: list):
        columns = dict()
        for name in column_names:
            columns[name] = list()
        for idx in range(len(records)):
            row = records[idx]
            # columns['idx'].append(idx)
            for name, value in row.items():
                columns[name].append(value)
        self.size = len(records)
        return columns

    def reload(self, records):
        self.columns = self.load(self.column_names, records)
        self.displayed_columns = self.load(self.displayed_column_names, records)
        self.last_actions = []
        self.displayed_last_actions = []
        self.deletion_record = []
        return self.check_consistency()

    def save_progress(self):
        self.last_actions = []
        self.displayed_last_actions = []
        self.deletion_record = []
        return self.check_consistency() and self.check_displayed_consistency()

    def check_schema(self, record: dict):
        for column_name in record.keys():
            if column_name not in self.column_names:
                print(f'Schema of Inserted Tuple does not match the Schema specified by the user!')
                return False
        for column in self.column_names:
            if column != 'idx':
                if column not in record.keys():
                    print(f'Schema of Inserted Tuple does not match the Schema specified by the user!')
                    return False
        return True

    def check_selected_column(self, column_names: list):
        for column in column_names:
            if column not in self.column_names:
                return False
        return True

    def check_consistency(self):
        schema1 = list(self.columns.keys())
        schema2 = list(self.column_names)
        schema1.sort()
        schema2.sort()
        return schema1 == schema2

    def check_displayed_consistency(self):
        schema1 = list(self.displayed_columns.keys())
        schema2 = list(self.displayed_column_names)
        schema1.sort()
        schema2.sort()
        return schema1 == schema2

    def update(self, idx, column: str, value, revert=False):
        if not revert:
            self.last_actions.append(Action(idx, prev=self.columns[column][idx], current=value, column=column))
        self.columns[column][idx] = value
        if not revert:
            self.displayed_last_actions.append(Action(idx, prev=self.displayed_columns[column][idx], current=value, column=column))
        self.displayed_columns[column][idx] = value

    def delete(self, idx, revert=False):
        if isinstance(idx, int):
            for column in self.column_names:
                self.delete_column(idx, column, revert)
            self.size -= 1
        if isinstance(idx, list):
            if idx:
                idx.sort()
                for i in reversed(idx):
                    self.delete(i, revert)
                self.deletion_record.append(idx)
            else:
                return False
        return True

    def delete_column(self, idx, column, revert=False):
        if not revert:
            self.last_actions.append(Action(idx, prev=self.columns[column][idx], column=column))
        self.columns[column].pop(idx)
        if column in self.displayed_column_names:
            if not revert:
                self.displayed_last_actions.append(Action(idx, prev=self.displayed_columns[column][idx], column=column))
            self.displayed_columns[column].pop(idx)

    def insert(self, idx, record: dict, revert=False):
        if self.check_schema(record):
            for column in self.column_names:
                self.insert_column(idx, column, record[column], revert)
            self.size += 1

    def insert_column(self, idx, column, value, revert=False):
        if not revert:
            self.last_actions.append(Action(idx, current=value, column=column))
        self.columns[column].insert(idx, value)
        if column in self.displayed_column_names:
            if not revert:
                self.displayed_last_actions.append(Action(idx, current=value, column=column))
            self.displayed_columns[column].insert(idx, value)

    def revert(self):
        if not self.last_actions or not self.displayed_last_actions:
            return None
        action = self.last_actions[-1]
        display_action = self.displayed_last_actions[-1]
        if action.type == 'Deletion':
            deleted_indices = self.deletion_record.pop(-1)
            for idx in deleted_indices:
                record = dict()
                while action.idx == idx and action.type == 'Deletion':
                    record[action.column] = action.prev
                    self.last_actions.pop(-1)
                    if not self.last_actions:
                        break
                    action = self.last_actions[-1]
                while display_action.idx == idx and display_action.type == 'Deletion':
                    if not self.displayed_last_actions:
                        break
                    display_action = self.displayed_last_actions.pop(-1)
                self.insert(idx, record, revert=True)
        elif action.type == 'Insertion':
            self.delete(action.idx, revert=True)
            idx = action.idx
            while action.idx == idx and action.type == 'Insertion':
                action = self.last_actions.pop(-1)
            while display_action.idx == idx and display_action.type == 'Insertion':
                display_action = self.displayed_last_actions.pop(-1)
        elif action.type == 'Modification':
            self.update(action.idx, action.column, action.prev, revert=True)
            self.last_actions.pop(-1)
            self.displayed_last_actions.pop(-1)
        else:
            print(f'Action has type None!')
            return None
        return action.type

    def change_display_columns(self, selected_columns: list):
        if selected_columns:
            assert self.check_selected_column(selected_columns)
            self.displayed_columns = dict()
            for column in selected_columns:
                self.displayed_columns[column] = list(self.columns[column])
            self.displayed_column_names = list(self.displayed_columns.keys())
            return True
        else:
            return False

    def to_schema(self):
        schema = []
        for column in self.displayed_column_names:
            if column != 'idx':
                schema.append(column)
        return schema

    def to_dict(self):
        assert self.check_displayed_consistency()
        rows = []
        for idx in range(self.size):
            row = dict()
            for name in self.displayed_column_names:
                if name != 'idx':
                    row[name] = self.displayed_columns[name][idx]
            rows.append(row)

        return rows
