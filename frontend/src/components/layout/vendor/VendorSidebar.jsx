import { useNavigate } from 'react-router-dom';
import { MenuItemLink, useSidebarState } from 'react-admin';
import { Box, Drawer, List } from '@mui/material';
import {
  Dashboard as DashboardIcon,
  ListAlt as ProductIcon,
  AddBox as AddProductIcon,
  List as OrdersIcon,
  Logout as LogoutIcon
} from '@mui/icons-material';

const VendorSidebar = () => {
  const navigate = useNavigate();
  const [open] = useSidebarState();

  return (
    <Drawer variant="permanent" open={open}>
      <Box sx={{ width: 250, mt: 2 }}>
        <List>
          <MenuItemLink to="/vendor/dashboard" primaryText="Dashboard" leftIcon={<DashboardIcon />} />
          <MenuItemLink to="/vendor/products" primaryText="My Products" leftIcon={<ProductIcon />} />
          <MenuItemLink to="/vendor/products/create" primaryText="Add Product" leftIcon={<AddProductIcon />} />
          <MenuItemLink to="/vendor/orders" primaryText="Orders" leftIcon={<OrdersIcon />} />
          <MenuItemLink to="/logout" primaryText="Logout" leftIcon={<LogoutIcon />} />
        </List>
      </Box>
    </Drawer>
  );
};

export default VendorSidebar;
