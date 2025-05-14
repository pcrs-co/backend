import { List, Datagrid, TextField, NumberField, EditButton } from 'react-admin';

const CPUBenchmarkList = () => (
    <List>
        <Datagrid rowClick="edit">
            <TextField source="id" />
            <TextField source="cpu" />
            <TextField source="cpu_mark" />
            <NumberField source="score" />
            <NumberField source="price" />
            <EditButton />
        </Datagrid>
    </List>
);

export default CPUBenchmarkList;
