import { List, Datagrid, TextField, NumberField, DateField, ReferenceField } from 'react-admin';

const VendorOrders = () => {
  return (
    <List resource="orders" title="Customer Orders" perPage={10}>
      <Datagrid rowClick="show">
        <TextField source="id" />
        <ReferenceField source="productId" reference="products" link="show">
          <TextField source="name" />
        </ReferenceField>
        <TextField source="customerName" />
        <NumberField source="quantity" />
        <NumberField source="totalPrice" options={{ style: 'currency', currency: 'USD' }} />
        <DateField source="orderDate" />
        <TextField source="status" />
      </Datagrid>
    </List>
  );
};

export default VendorOrders;
