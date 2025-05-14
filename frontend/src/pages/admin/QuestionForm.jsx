import { Create, Edit, SimpleForm, TextInput, SelectInput, ArrayInput, SimpleFormIterator } from 'react-admin';

export const QuestionCreate = () => (
    <Create>
        <SimpleForm>
            <TextInput source="slug" />
            <TextInput source="question_text" label="Question Text" />
            <SelectInput source="question_type" choices={[
                { id: 'choice', name: 'Multiple Choice' },
                { id: 'text', name: 'Text Input' },
                { id: 'boolean', name: 'Yes/No' },
                { id: 'scale', name: 'Scale (1-5)' },
            ]} />
            <TextInput source="options" label="Options (JSON format)" />
        </SimpleForm>
    </Create>
);

export const QuestionEdit = () => (
    <Edit>
        <SimpleForm>
            <TextInput source="slug" />
            <TextInput source="question_text" label="Question Text" />
            <SelectInput source="question_type" choices={[
                { id: 'choice', name: 'Multiple Choice' },
                { id: 'text', name: 'Text Input' },
                { id: 'boolean', name: 'Yes/No' },
                { id: 'scale', name: 'Scale (1-5)' },
            ]} />
            <TextInput source="options" label="Options (JSON format)" />
        </SimpleForm>
    </Edit>
);
