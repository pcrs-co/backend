import {
    Create,
    Edit,
    SimpleForm,
    TextInput,
    required
  } from 'react-admin';
  
  // Shared form layout
  const VendorFormFields = () => (
    <>
      <TextInput source="name" label="Vendor Name" validate={required()} fullWidth />
      <TextInput source="email" label="Email" type="email" fullWidth />
      <TextInput source="phone" label="Phone Number" fullWidth />
    </>
  );
  
  // Create vendor
  export const VendorCreate = () => (
    <Create>
      <SimpleForm>
        <VendorFormFields />
      </SimpleForm>
    </Create>
  );
  
  // Edit vendor
  export const VendorEdit = () => (
    <Edit>
      <SimpleForm>
        <VendorFormFields />
      </SimpleForm>
    </Edit>
  );
  