import { List, Datagrid, TextField, NumberField, EditButton } from 'react-admin';

const GPUBenchmarkList = () => (
    <List>
        <Datagrid>
            <TextField source="id" />
            <TextField source="name" />
            <NumberField source="benchmark_score" />
            <EditButton />
        </Datagrid>
    </List>
);

export default GPUBenchmarkList;
