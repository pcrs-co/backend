import { Create, Edit, SimpleForm, TextInput, NumberInput } from 'react-admin';

export const CPUBenchmarkCreate = () => (
    <Create>
        <SimpleForm>
            <TextInput source="cpu" />
            <TextInput source="cpu_mark" />
            <NumberInput source="score" />
            <NumberInput source="price" />
        </SimpleForm>
    </Create>
);

export const CPUBenchmarkEdit = () => (
    <Edit>
        <SimpleForm>
            <TextInput source="cpu" />
            <TextInput source="cpu_mark" />
            <NumberInput source="score" />
            <NumberInput source="price" />
        </SimpleForm>
    </Edit>
);
