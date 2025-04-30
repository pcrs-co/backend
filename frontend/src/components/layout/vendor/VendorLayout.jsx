import { Admin, Resource, Layout } from 'react-admin';
import fakeDataProvider from 'ra-data-fakerest'; // or your actual data provider
import VendorSidebar from './VendorSidebar';
import VendorAppbar from './VendorAppbar';
import ProductList from '../../../pages/vendor/ProductList';
import { ProductCreate, ProductEdit } from '../../../pages/vendor/ProductForm';

const dataProvider = fakeDataProvider({
  products: [
    { id: 1, name: 'Example Device 1' },
    { id: 2, name: 'Example Device 2' },
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
      {/* Add more <Resource> entries if needed */}
    </Admin>
  );
};

export default VendorLayout;
