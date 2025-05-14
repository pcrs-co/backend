import { Create, Edit, SimpleForm, TextInput, NumberInput } from 'react-admin';

export const GPUBenchmarkCreate = () => (
  <Create>
    <SimpleForm>
      <TextInput source="name" />
      <NumberInput source="benchmark_score" />
    </SimpleForm>
  </Create>
);

export const GPUBenchmarkEdit = () => (
  <Edit>
    <SimpleForm>
      <TextInput source="name" />
      <NumberInput source="benchmark_score" />
    </SimpleForm>
  </Edit>
);
