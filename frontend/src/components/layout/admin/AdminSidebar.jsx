import { MenuItemLink, useSidebarState } from 'react-admin';
import { Box, Drawer, List } from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Store as VendorIcon,
  People as CustomerIcon,
  Inventory as ProductIcon,
  Assignment as OrderIcon,
  Apps as ApplicationIcon,
  Memory as CpuIcon,
  GraphicEq as GpuIcon,
  Logout as LogoutIcon
} from '@mui/icons-material';

const AdminSidebar = () => {
  const [open] = useSidebarState();

  return (
    <Drawer variant="permanent" open={open}>
      <Box sx={{ width: 250, mt: 2 }}>
        <List>
          <MenuItemLink to="/admin/dashboard" primaryText="Dashboard" leftIcon={<DashboardIcon />} />
          <MenuItemLink to="/admin/vendors" primaryText="Vendors" leftIcon={<VendorIcon />} />
          <MenuItemLink to="/admin/customers" primaryText="Customers" leftIcon={<CustomerIcon />} />
          <MenuItemLink to="/admin/products" primaryText="Products" leftIcon={<ProductIcon />} />
          <MenuItemLink to="/admin/orders" primaryText="Orders" leftIcon={<OrderIcon />} />
          <MenuItemLink to="/admin/applications" primaryText="Applications" leftIcon={<ApplicationIcon />} />
          <MenuItemLink to="/admin/cpu-benchmarks" primaryText="CPU Benchmarks" leftIcon={<CpuIcon />} />
          <MenuItemLink to="/admin/gpu-benchmarks" primaryText="GPU Benchmarks" leftIcon={<GpuIcon />} />
          <MenuItemLink to="/logout" primaryText="Logout" leftIcon={<LogoutIcon />} />
        </List>
      </Box>
    </Drawer>
  );
};

export default AdminSidebar;
