import { Create, Edit, SimpleForm, TextInput } from 'react-admin';

export const ApplicationCreate = () => (
    <Create>
        <SimpleForm>
            <TextInput source="name" />
            <TextInput source="description" multiline />
            <TextInput source="min_requirements" multiline />
            <TextInput source="recommended_requirements" multiline />
        </SimpleForm>
    </Create>
);

export const ApplicationEdit = () => (
    <Edit>
        <SimpleForm>
            <TextInput source="name" />
            <TextInput source="description" multiline />
            <TextInput source="min_requirements" multiline />
            <TextInput source="recommended_requirements" multiline />
        </SimpleForm>
    </Edit>
);
