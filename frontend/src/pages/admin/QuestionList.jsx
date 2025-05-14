import { List, Datagrid, TextField, EditButton } from 'react-admin';

const QuestionList = () => (
    <List>
        <Datagrid rowClick="edit">
            <TextField source="id" />
            <TextField source="text" />
            <EditButton />
        </Datagrid>
    </List>
);

export default QuestionList;
