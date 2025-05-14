import { AppBar } from 'react-admin';
import { Typography, Box } from '@mui/material';

const AdminAppBar = () => (
  <AppBar>
    <Box sx={{ flex: 1, textAlign: 'center' }}>
      <Typography variant="h6">Admin Panel</Typography>
    </Box>
  </AppBar>
);

export default AdminAppBar;
