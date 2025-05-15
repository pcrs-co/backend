import { Admin, Resource, Layout } from 'react-admin';
import dataProvider from '../../../utils/dataProvider';
import AdminSidebar from './AdminSidebar';
import AdminAppbar from './AdminAppbar';

import QuestionList from '../../../pages/admin/QuestionList';
import { QuestionCreate, QuestionEdit } from '../../../pages/admin/QuestionForm';
import ActivityList from '../../../pages/admin/ActivityList';
import { ActivityCreate, ActivityEdit } from '../../../pages/admin/ActivityForm';
import ApplicationList from '../../../pages/admin/ApplicationList';
import { ApplicationCreate, ApplicationEdit } from '../../../pages/admin/ApplicationForm';
import CPUBenchmarkList from '../../../pages/admin/CPUBenchmarkList';
import { CPUBenchmarkCreate, CPUBenchmarkEdit } from '../../../pages/admin/CPUBenchmarkForm';
import GPUBenchmarkList from '../../../pages/admin/GPUBenchmarkList';
import { GPUBenchmarkCreate, GPUBenchmarkEdit } from '../../../pages/admin/GPUBenchmarkForm';
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
      <Resource
        name="questions"
        list={QuestionList}
        create={QuestionCreate}
        edit={QuestionEdit}
        options={{ label: 'Questions' }}
      />
      <Resource
        name="activities"
        list={ActivityList}
        create={ActivityCreate}
        edit={ActivityEdit}
        options={{ label: 'Activities' }}
      />
      <Resource
        name="applications"
        list={ApplicationList}
        create={ApplicationCreate}
        edit={ApplicationEdit}
        options={{ label: 'Applications' }}
      />
      <Resource
        name="cpu_benchmarks"
        list={CPUBenchmarkList}
        create={CPUBenchmarkCreate}
        edit={CPUBenchmarkEdit}
        options={{ label: 'CPU Benchmarks' }}
      />
      <Resource
        name="gpu_benchmarks"
        list={GPUBenchmarkList}
        create={GPUBenchmarkCreate}
        edit={GPUBenchmarkEdit}
        options={{ label: 'GPU Benchmarks' }}
      />
    </Admin>
  );
};

export default AdminLayout;
