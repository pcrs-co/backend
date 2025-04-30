import { AppBar } from 'react-admin';
import { Typography, Box } from '@mui/material';

const VendorAppBar = () => (
  <AppBar>
    <Box sx={{ flex: 1, textAlign: 'center' }}>
      <Typography variant="h6">Vendor Panel</Typography>
    </Box>
  </AppBar>
);

export default VendorAppBar;
