import { Admin, Resource } from "react-admin";
import fakeDataProvider from "ra-data-fakerest";
import "./App.css";
import {
  VideoCreate,
  VideoEdit,
  VideoList,
  VideoShow,
} from "./pages/VideoRequests";
import {
  VideoTemplateCreate,
  VideoTemplateEdit,
  VideoTemplateList,
  VideoTemplateShow,
} from "./pages/VideoTemplates";

const dataProvider = fakeDataProvider({
  videos: [
    { id: 0, title: "Hello, world!" },
    { id: 1, title: "FooBar" },
  ],
  video_templates: [
    { id: 0, title: "Hello, world!" },
    { id: 1, title: "FooBar" },
  ],
});

function App() {
  return (
    <div className="App">
      <Admin dataProvider={dataProvider}>
        <Resource
          name="videos"
          create={VideoCreate}
          list={VideoList}
          show={VideoShow}
          edit={VideoEdit}
        />
        <Resource
          name="video_templates"
          create={VideoTemplateCreate}
          list={VideoTemplateList}
          show={VideoTemplateShow}
          edit={VideoTemplateEdit}
        />
      </Admin>
    </div>
  );
}

export default App;
