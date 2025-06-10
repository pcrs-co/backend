import { Admin, Resource, Layout } from 'react-admin';
import fakeDataProvider from 'ra-data-fakerest';
import VendorAppbar from './VendorAppbar';
import ProductList from '../../../pages/vendor/ProductList';
import VendorOrders from '../../../pages/vendor/VendorOrders';
import { ProductCreate, ProductEdit } from '../../../pages/vendor/ProductForm';

const dataProvider = fakeDataProvider({
  products: [
    { id: 1, name: 'Example Device 1' },
    { id: 2, name: 'Example Device 2' },
  ],
  orders: [
    { id: 1, customer: 'John Doe', product: 'Example Device 1', quantity: 2, ordered_at: new Date(), status: 'Pending' },
    { id: 2, customer: 'Jane Smith', product: 'Example Device 2', quantity: 1, ordered_at: new Date(), status: 'Shipped' },
  ],
});


const CustomLayout = (props) => (
  <Layout
    {...props}
    appBar={VendorAppbar}
    menu={VendorSidebar}
  />
);

const VendorLayout = () => {
  return (
    <Admin
      layout={CustomLayout}
      dataProvider={dataProvider}
      basename="/vendor"
    >
      <Resource
        name="products"
        list={ProductList}
        create={ProductCreate}
        edit={ProductEdit}
        options={{ label: 'My Products' }}
      />
      <Resource
        name="orders"
        list={VendorOrders}
        options={{ label: 'Orders' }}
      />
    </Admin>
  );
};

export default VendorLayout;
