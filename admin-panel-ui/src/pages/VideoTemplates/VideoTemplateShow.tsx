import {
  DateField,
  NumberField,
  Show,
  SimpleShowLayout,
  TextField,
} from "react-admin";

export const VideoTemplateShow = (props: any) => (
  <Show {...props}>
    <SimpleShowLayout>
      <TextField source="title" />
      <TextField source="description" />
      <NumberField source="duration" />
      <DateField source="published_at" />
    </SimpleShowLayout>
  </Show>
);
