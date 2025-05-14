import { List, Datagrid, TextField, EditButton } from 'react-admin';

const ApplicationList = () => (
    <List>
        <Datagrid>
            <TextField source="id" />
            <TextField source="name" />
            <TextField source="description" />
            <TextField source="min_requirements" />
            <TextField source="recommended_requirements" />
            <EditButton />
        </Datagrid>
    </List>
);

export default ApplicationList;
