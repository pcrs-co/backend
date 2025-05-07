import { List, Datagrid, TextField, EmailField, UrlField } from 'react-admin';

const VendorList = () => (
  <List>
    <Datagrid rowClick="edit">
      <TextField source="id" />
      <TextField source="company_name" />
      <TextField source="first_name" />
      <TextField source="last_name" />
      <TextField source="username" />
      <EmailField source="email" />
      <TextField source="phone_number" />
      <TextField source="location" />
      <TextField source="region" />
      <TextField source="district" />
      <UrlField source="logo" label="Logo URL" />
    </Datagrid>
  </List>
);

export default VendorList;
