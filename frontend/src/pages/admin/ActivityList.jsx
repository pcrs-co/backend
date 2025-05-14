import { List, Datagrid, TextField, EditButton } from 'react-admin';

const ActivityList = () => (
  <List>
    <Datagrid rowClick="edit">
      <TextField source="id" />
      <TextField source="name" />
      <EditButton />
    </Datagrid>
  </List>
);

export default ActivityList;
