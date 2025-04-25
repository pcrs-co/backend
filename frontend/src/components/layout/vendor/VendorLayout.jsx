import { Outlet } from 'react-router-dom';
import VendorSidebar from './VendorSidebar';
import VendorAppbar from './VendorAppbar';

const VendorLayout = () => {
  return (
    <div className="vendor-layout" style={{ display: 'flex' }}>
      <VendorSidebar />
      <div className="main-content" style={{ flex: 1 }}>
        <VendorAppbar />
        <div style={{ padding: '1rem' }}>
          <Outlet /> {/* This renders the nested routes */}
        </div>
      </div>
    </div>
  );
};

export default VendorLayout;
