import { List, Datagrid, TextField, EditButton } from 'react-admin';

const QuestionList = () => (
    <List>
        <Datagrid rowClick="edit">
            <TextField source="id" />
            <TextField source="slug" />
            <TextField source="question_text" label="Question Text" />
            <TextField source="question_type" />
            <TextField source="options" />
            <EditButton />
        </Datagrid>
    </List>
);

export default QuestionList;
