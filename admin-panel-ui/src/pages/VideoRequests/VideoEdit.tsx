import { DateInput, Edit, NumberInput, SimpleForm, TextInput } from "react-admin";

export const VideoEdit = (props: any) => (
  <Edit {...props}>
    <SimpleForm>
      <TextInput source="title" />
      <TextInput source="description" />
      <NumberInput source="duration" />
      <DateInput source="published_at" />
    </SimpleForm>
  </Edit>
);
