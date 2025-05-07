// CustomerList.jsx
import { List, Datagrid, TextField } from 'react-admin';

const CustomerList = () => (
  <List>
    <Datagrid rowClick="edit">
      <TextField source="id" />
      <TextField source="name" />
    </Datagrid>
  </List>
);

export default CustomerList;
