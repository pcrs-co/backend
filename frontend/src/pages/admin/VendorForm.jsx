import {
    Create,
    Edit,
    SimpleForm,
    TextInput,
    required,
    ImageInput,
    ImageField
  } from 'react-admin';
  
  // Shared form fields for Create and Edit
  const VendorFormFields = () => (
    <>
      <TextInput source="company_name" label="Company Name" validate={required()} fullWidth />
      <TextInput source="first_name" label="First Name" validate={required()} fullWidth />
      <TextInput source="last_name" label="Last Name" validate={required()} fullWidth />
      <TextInput source="username" label="Username" validate={required()} fullWidth />
      <TextInput source="email" label="Email" type="email" validate={required()} fullWidth />
      <TextInput source="phone_number" label="Phone Number" validate={required()} fullWidth />
      <TextInput source="location" label="Location" fullWidth />
      <TextInput source="region" label="Region" fullWidth />
      <TextInput source="district" label="District" fullWidth />
  
      <ImageInput source="logo" label="Vendor Logo" accept="image/*">
        <ImageField source="src" title="title" />
      </ImageInput>
    </>
  );
  
  // Create Vendor
  export const VendorCreate = () => (
    <Create>
      <SimpleForm>
        <VendorFormFields />
      </SimpleForm>
    </Create>
  );
  
  // Edit Vendor
  export const VendorEdit = () => (
    <Edit>
      <SimpleForm>
        <VendorFormFields />
      </SimpleForm>
    </Edit>
  );
  