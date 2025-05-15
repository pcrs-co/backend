import { Create, Edit, SimpleForm, TextInput, ReferenceInput, SelectInput } from 'react-admin';

export const ApplicationCreate = () => (
    <Create>
        <SimpleForm>
            <TextInput source="name" required />
            <ReferenceInput source="activity" reference="activities">
                <SelectInput optionText="name" />
            </ReferenceInput>
            <SelectInput source="intensity_level" choices={[
                { id: 'low', name: 'Low' },
                { id: 'medium', name: 'Medium' },
                { id: 'high', name: 'High' },
            ]} />
            <TextInput source="source" />
        </SimpleForm>
    </Create>
);

export const ApplicationEdit = () => (
    <Edit>
        <SimpleForm>
            <TextInput source="name" required />
            <ReferenceInput source="activity" reference="activities">
                <SelectInput optionText="name" />
            </ReferenceInput>
            <SelectInput source="intensity_level" choices={[
                { id: 'low', name: 'Low' },
                { id: 'medium', name: 'Medium' },
                { id: 'high', name: 'High' },
            ]} />
            <TextInput source="source" />
        </SimpleForm>
    </Edit>
);
