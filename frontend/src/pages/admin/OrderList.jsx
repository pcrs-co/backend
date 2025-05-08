import { List, Datagrid, TextField, ReferenceField } from 'react-admin';

const OrderList = () => (
  <List>
    <Datagrid rowClick="edit">
      <TextField source="id" />
      <ReferenceField source="customer_id" reference="customers" />
      <ReferenceField source="product_id" reference="products" />
      <TextField source="status" />
    </Datagrid>
  </List>
);

export default OrderList;
