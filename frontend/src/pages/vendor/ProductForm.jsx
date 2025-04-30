// frontend/src/pages/vendor/ProductForm.jsx
import {
  Create,
  Edit,
  SimpleForm,
  TextInput,
  NumberInput,
  required,
} from 'react-admin';

const ProductFormFields = () => (
  <SimpleForm>
    <TextInput source="name" validate={required()} fullWidth />
    <TextInput source="description" multiline fullWidth />
    <NumberInput source="price" validate={required()} />
  </SimpleForm>
);

export const ProductCreate = () => <Create><ProductFormFields /></Create>;

export const ProductEdit = () => <Edit><ProductFormFields /></Edit>;
