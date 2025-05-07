import { List, Datagrid, TextField } from 'react-admin';

const VendorList = () => (
  <List>
    <Datagrid rowClick="edit">
      <TextField source="id" />
      <TextField source="name" />
    </Datagrid>
  </List>
);

export default VendorList;
