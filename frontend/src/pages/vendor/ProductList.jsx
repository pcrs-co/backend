// frontend/src/pages/vendor/ProductList.jsx
import { List, Datagrid, TextField, EditButton, DeleteButton } from 'react-admin';

const ProductList = () => (
  <List>
    <Datagrid rowClick="edit">
      <TextField source="id" />
      <TextField source="name" />
      <TextField source="description" />
      <TextField source="price" />
      <EditButton />
      <DeleteButton />
    </Datagrid>
  </List>
);

export default ProductList;
