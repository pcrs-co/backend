import { Admin, Resource, Layout } from 'react-admin';
import dataProvider from '../../../utils/dataProvider';
import AdminSidebar from './AdminSidebar';
import AdminAppbar from './AdminAppbar';

import VendorList from '../../../pages/admin/VendorList';
import { VendorCreate, VendorEdit } from '../../../pages/admin/VendorForm';
import CustomerList from '../../../pages/admin/CustomerList';
import ProductList from '../../../pages/admin/ProductList';
import OrderList from '../../../pages/admin/OrderList';
import Dashboard from '../../../pages/admin/Dashboard';

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
      <Resource name="order" list={OrderList} options={{ label: 'Orders' }} />
    </Admin>
  );
};

export default AdminLayout;
