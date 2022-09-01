import torch
import torchvision
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor

device = torch.device('cpu')  

model = torchvision.models.detection.maskrcnn_resnet50_fpn(pretrained=True) 
in_features = model.roi_heads.box_predictor.cls_score.in_features
model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes=2)
hidden_layer = 256
model.roi_heads.mask_predictor = MaskRCNNPredictor(in_features_mask,
                                                        hidden_layer,
                                                        num_classes)
# model.load_state_dict(torch.load("state_model.pt", map_location="cpu"))
# model.eval()

# imgPath = 'test_sample.jpg'

# images=cv2.imread(imgPath)
# images = cv2.resize(images, imageSize, cv2.INTER_LINEAR)
# images = torch.as_tensor(images, dtype=torch.float32).unsqueeze(0)
# images=images.swapaxes(1, 3).swapaxes(2, 3)
# images = list(image.to(device) for image in images)x``

# with torch.no_grad():
#     pred = model(images)
#     print(pred)

# im= images[0].swapaxes(0, 2).swapaxes(0, 1).detach().cpu().numpy().astype(np.uint8)
# im2 = im.copy()
# for i in range(len(pred[0]['masks'])):
#     msk=pred[0]['masks'][i,0].detach().cpu().numpy()
#     scr=pred[0]['scores'][i].detach().cpu().numpy()
#     if scr>0.8 :
#         im2[:,:,0][msk>0.5] = random.randint(0,255)
#         im2[:, :, 1][msk > 0.5] = random.randint(0,255)
#         im2[:, :, 2][msk > 0.5] = random.randint(0, 255)
# cv2.imshow(str(scr), np.hstack([im,im2]))
# cv2.waitKey()