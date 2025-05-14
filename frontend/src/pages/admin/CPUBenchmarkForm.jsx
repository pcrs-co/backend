import { Create, Edit, SimpleForm, TextInput, NumberInput } from 'react-admin';

export const CPUBenchmarkCreate = () => (
    <Create>
        <SimpleForm>
            <TextInput source="name" />
            <NumberInput source="benchmark_score" />
        </SimpleForm>
    </Create>
);

export const CPUBenchmarkEdit = () => (
    <Edit>
        <SimpleForm>
            <TextInput source="name" />
            <NumberInput source="benchmark_score" />
        </SimpleForm>
    </Edit>
);
