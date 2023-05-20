import { List, Datagrid, TextField, NumberField, DateField } from "react-admin";

export const VideoList = (props: any) => (
  <List {...props}>
    <Datagrid rowClick="edit">
      <TextField source="id" />
      <TextField source="title" />
      <TextField source="description" />
      <NumberField source="duration" />
      <DateField source="published_at" />
    </Datagrid>
  </List>
);
