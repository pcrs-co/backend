import { Create, Edit, SimpleForm, TextInput } from 'react-admin';

export const QuestionCreate = () => (
    <Create>
        <SimpleForm>
            <TextInput source="text" label="Question Text" />
        </SimpleForm>
    </Create>
);

export const QuestionEdit = () => (
    <Edit>
        <SimpleForm>
            <TextInput source="text" label="Question Text" />
        </SimpleForm>
    </Edit>
);
