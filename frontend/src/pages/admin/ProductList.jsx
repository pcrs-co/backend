import { List, Datagrid, TextField, ReferenceField } from 'react-admin';

const ProductList = () => (
  <List>
    <Datagrid rowClick="edit">
      <TextField source="id" />
      <TextField source="name" />
      <ReferenceField source="vendor_id" reference="vendors" />
    </Datagrid>
  </List>
);

export default ProductList;
