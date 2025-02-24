import json
import lark_oapi as lark
from lark_oapi.api.bitable.v1 import *
from lark_oapi.api.drive.v1 import *
import os


class TableDealer:
    
    def __init__(self, image_dir = "temp/", index = 0):
        self.image_dir = os.path.join(os.getcwd(), image_dir)
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)
        
        self.client = lark.Client.builder() \
            .enable_set_token(True) \
            .log_level(lark.LogLevel.DEBUG) \
            .build()
            
        self.option = lark.RequestOption.builder().user_access_token(os.getenv("USER_ACCESS_TOKEN")).build()
        self.index = index
            
            
    def getNewItems(self, batch_size = 50):
        request: SearchAppTableRecordRequest = SearchAppTableRecordRequest.builder() \
            .app_token(os.getenv('APP_TOKEN')) \
            .table_id(os.getenv('TABLE_ID')) \
            .user_id_type("open_id") \
            .page_size(batch_size) \
            .request_body(SearchAppTableRecordRequestBody.builder()
                .view_id(os.getenv('VIEW_ID'))
                .field_names(["产品品类", "主题编号", "预览小图"])
                .filter(FilterInfo.builder()
                    .conjunction("and")
                    .conditions([Condition.builder()
                        .field_name("产品名字英文")
                        .operator("isEmpty")
                        .value([])
                        .build(), 
                        Condition.builder()
                        .field_name("预览小图")
                        .operator("isNotEmpty")
                        .value([])
                        .build()
                        ])
                    .build())
                .automatic_fields(False)
                .build()) \
            .build()

        response: SearchAppTableRecordResponse = self.client.bitable.v1.app_table_record.search(request, self.option)

        if not response.success():
            lark.logger.error(
                f"client.bitable.v1.app_table_record.search failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
            return

        lark.logger.info(lark.JSON.marshal(response.data, indent=4))
        output_file = os.path.join(self.image_dir, "new_items_" + str(self.index) + ".json")
        with open(output_file, 'w', encoding="utf-8") as file:
            file.write(lark.JSON.marshal(response.data, indent=4))
            self.index += 1
        
        return response.data.items
        
        
    def downloadImages(self, items):
        image_filenames = []
        
        for item in items:
            fields = item.fields
            request: DownloadMediaRequest = DownloadMediaRequest.builder() \
                .file_token(fields["预览小图"][0]["file_token"]) \
                .build()

            response: DownloadMediaResponse = self.client.drive.v1.media.download(request, self.option)

            if not response.success():
                lark.logger.error(
                    f"client.drive.v1.media.download failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
                return
            
            image_filename = fields["产品品类"] + str(fields["主题编号"]) + ".jpg"
            with open(os.path.join(self.image_dir, image_filename), 'wb') as file:
                file.write(response.file.read())
                file.close()
            image_filenames.append(image_filename)
            print("Downloaded image ", image_filename)
        
        return image_filenames

