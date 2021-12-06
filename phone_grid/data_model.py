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
        self.column_names.insert(0, 'idx')
        self.columns = self.load(column_names, records)
        self.displayed_column_names = self.column_names
        self.displayed_columns = self.columns
        self.size = len(records)
        self.last_actions = []
        self.displayed_last_actions = []
        assert self.check_consistency()

    def load(self, column_names: list, records: list):
        columns = dict()
        for name in column_names:
            columns[name] = list()
        for idx in range(len(records)):
            row = records[idx]
            columns['idx'].append(idx)
            for name, value in row.items():
                columns[name].append(value)
        return columns

    def reload(self, records):
        self.columns = self.load(self.column_names, records)
        self.displayed_columns = self.columns
        self.last_actions = []

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
        schema2 = self.column_names
        schema1.sort()
        schema2.sort()
        return schema1 == schema2

    def check_displayed_consistency(self):
        schema1 = list(self.displayed_columns.keys())
        schema2 = self.displayed_column_names
        schema1.sort()
        schema2.sort()
        return schema1 == schema2

    def update(self, idx, column: str, value, revert=False):
        if not revert:
            self.last_actions.append(Action(idx, self.columns[column][idx], value, column))
        self.columns[column][idx] = value
        if not revert:
            self.displayed_last_actions.append(Action(idx, self.displayed_columns[column][idx], value, column))
        self.displayed_columns[column][idx] = value

    def delete_column(self, idx, column, revert=False):
        if not revert:
            self.last_actions.append(Action(idx, self.columns[column][idx], column))
        self.columns[column].pop(idx)
        if column not in self.displayed_column_names:
            if not revert:
                self.displayed_last_actions.append(Action(idx, self.displayed_columns[column][idx], column))
            self.displayed_columns[column].pop(idx)

    def delete(self, idx, revert=False):
        if isinstance(idx, int):
            for column in self.column_names:
                self.delete_column(idx, column, revert)
            self.size -= 1
        if isinstance(idx, list):
            for i in idx:
                self.delete(i, revert)

    def insert(self, idx, record: dict, revert=False):
        if self.check_schema(record):
            for column in self.column_names:
                self.insert_column(idx, column, record[column], revert)
            self.size += 1

    def insert_column(self, idx, column, value, revert=False):
        if not revert:
            self.last_actions.append(Action(idx, current=value, column=column))
        self.columns[column][idx] = value
        if column not in self.displayed_column_names:
            if not revert:
                self.displayed_last_actions.append(Action(idx, current=value, column=column))
            self.displayed_columns[column][idx] = value

    def revert(self):
        action = self.last_actions.pop(-1)
        if action.type == 'Deletion':
            idx = action.idx
            record = dict()
            record[action.column] = action.current
            while action.idx == idx:
                action = self.last_actions.pop(-1)
                record[action.column] = action.prev
            self.insert(idx, record, revert=True)
        elif action.type == 'Insertion':
            self.delete(action.idx, revert=True)
            idx = action.idx
            while action.idx == idx and action.type == 'Insertion':
                self.last_actions.pop(-1)
        elif action.type == 'Modification':
            self.update(action.idx, action.column, action.prev, revert=True)
            self.last_actions.pop(-1)
        else:
            print(f'Action has type None!')
            exit(-1)

    def change_display_column_names(self, selected_columns: list):
        for name in self.displayed_column_names:
            if name != 'idx':
                if name not in selected_columns:
                    self.displayed_column_names.pop(name)

    def change_display_columns(self, selected_columns: list):
        assert self.check_selected_column(selected_columns)

        self.change_display_column_names(selected_columns)

        self.displayed_columns = dict()
        for column in selected_columns:
            self.displayed_columns[column] = self.columns[column]

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
