import { Create, SimpleForm, TextInput, NumberInput, DateInput } from 'react-admin';

export const VideoTemplateCreate = (props: any) => (
    <Create {...props}>
        <SimpleForm>
            <TextInput source="title" />
            <TextInput source="description" />
            <NumberInput source="duration" />
            <DateInput source="published_at" />
        </SimpleForm>
    </Create>
);
