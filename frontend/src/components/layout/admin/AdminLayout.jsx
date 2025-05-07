import { Admin, Resource, Layout } from 'react-admin';
import fakeDataProvider from 'ra-data-fakerest';
import AdminSidebar from './AdminSidebar';
import AdminAppbar from './AdminAppbar';

import VendorList from '../../../pages/admin/VendorList';
import { VendorCreate, VendorEdit } from '../../../pages/admin/VendorForm';
import CustomerList from '../../../pages/admin/CustomerList';
import ProductList from '../../../pages/admin/ProductList';
import OrderList from '../../../pages/admin/OrderList';
import Dashboard from '../../../pages/admin/Dashboard';

const dataProvider = fakeDataProvider({
  vendors: [
    { id: 1, name: 'Vendor A' },
    { id: 2, name: 'Vendor B' },
  ],
  customers: [
    { id: 1, name: 'Customer A' },
    { id: 2, name: 'Customer B' },
  ],
  products: [
    { id: 1, name: 'Phone X', vendor_id: 1 },
    { id: 2, name: 'Laptop Y', vendor_id: 2 },
  ],
  orders: [
    { id: 1, customer_id: 1, product_id: 1, status: 'Pending' },
    { id: 2, customer_id: 2, product_id: 2, status: 'Delivered' },
  ],
});

const CustomLayout = (props) => (
  <Layout
    {...props}
    appBar={AdminAppbar}
    menu={AdminSidebar}
  />
);

const AdminLayout = () => {
  return (
    <Admin
      dashboard={Dashboard}
      layout={CustomLayout}
      dataProvider={dataProvider}
      basename="/admin"
    >
      <Resource
        name="vendors"
        list={VendorList}
        create={VendorCreate}
        edit={VendorEdit}
        options={{ label: 'Vendors' }}
      />
      <Resource name="customers" list={CustomerList} options={{ label: 'Customers' }} />
      <Resource name="products" list={ProductList} options={{ label: 'Products' }} />
      <Resource name="orders" list={OrderList} options={{ label: 'Orders' }} />
    </Admin>
  );
};

export default AdminLayout;
