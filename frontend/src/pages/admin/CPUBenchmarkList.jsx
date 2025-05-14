import { List, Datagrid, TextField, NumberField, EditButton } from 'react-admin';

const CPUBenchmarkList = () => (
  <List>
    <Datagrid>
      <TextField source="id" />
      <TextField source="name" />
      <NumberField source="benchmark_score" />
      <EditButton />
    </Datagrid>
  </List>
);

export default CPUBenchmarkList;
