import { List, Datagrid, TextField, EditButton, ReferenceField } from 'react-admin';

const ApplicationList = () => (
    <List>
        <Datagrid rowClick="edit">
            <TextField source="id" />
            <TextField source="name" />
            <ReferenceField source="activity" reference="activities">
                <TextField source="name" />
            </ReferenceField>
            <TextField source="intensity_level" />
            <TextField source="source" />
            <EditButton />
        </Datagrid>
    </List>
);

export default ApplicationList;
