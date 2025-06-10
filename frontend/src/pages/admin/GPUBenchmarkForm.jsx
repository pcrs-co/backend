import { Create, Edit, SimpleForm, TextInput, NumberInput } from 'react-admin';

export const GPUBenchmarkCreate = () => (
    <Create>
        <SimpleForm>
            <TextInput source="cpu" />
            <TextInput source="cpu_mark" />
            <NumberInput source="score" />
            <NumberInput source="price" />
        </SimpleForm>
    </Create>
);

export const GPUBenchmarkEdit = () => (
    <Edit>
        <SimpleForm>
            <TextInput source="cpu" />
            <TextInput source="cpu_mark" />
            <NumberInput source="score" />
            <NumberInput source="price" />
        </SimpleForm>
    </Edit>
);
