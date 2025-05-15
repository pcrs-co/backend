import {
    Create,
    Edit,
    SimpleForm,
    TextInput,
    SelectInput,
    Title,
} from 'react-admin';
import { Card, CardContent, Typography, Box } from '@mui/material';

const questionTypeChoices = [
    { id: 'choice', name: 'Multiple Choice' },
    { id: 'text', name: 'Text Input' },
    { id: 'boolean', name: 'Yes/No' },
    { id: 'scale', name: 'Scale (1-5)' },
];

const FormLayout = ({ isEdit = false }) => (
    <Card elevation={3} sx={{ p: 3, maxWidth: 700, mx: 'auto', my: 2 }}>
        <CardContent>
            <Typography variant="h6" gutterBottom>
                {isEdit ? 'Edit Question' : 'Create New Question'}
            </Typography>
            <SimpleForm>
                <Box mb={2}>
                    <TextInput source="slug" fullWidth label="Slug (unique ID)" />
                </Box>
                <Box mb={2}>
                    <TextInput source="question_text" fullWidth label="Question Text" multiline />
                </Box>
                <Box mb={2}>
                    <SelectInput
                        source="question_type"
                        label="Question Type"
                        choices={questionTypeChoices}
                        fullWidth
                    />
                </Box>
                <Box mb={2}>
                    <TextInput
                        source="options"
                        label="Options (in JSON, if applicable)"
                        fullWidth
                        multiline
                        helperText="e.g., ['Option A', 'Option B'] for multiple choice"
                    />
                </Box>
            </SimpleForm>
        </CardContent>
    </Card>
);

export const QuestionCreate = () => (
    <Create title="Create Question">
        <FormLayout isEdit={false} />
    </Create>
);

export const QuestionEdit = () => (
    <Edit title={<Title title="Edit Question" />}>
        <FormLayout isEdit={true} />
    </Edit>
);
