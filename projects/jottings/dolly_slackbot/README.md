# Your very own low-quality-fact bot

(Or whatever else you want it to be)

This flow takes an LLM prompt as input, and invokes the dolly-3b LLM produced by databricks to generate a response. The response is posted to slack via a slack hook.

The deployment assumes you are using kubernetes, and includes a kustomization to require quite a lot of memory (ref the big model).

In order to make this all work:

- Build and push the image located in `images/orion_dolly/` to a docker registry of your choice. Because this image contains the LLM, it is quite big. So you might have to be patient.
- Register a KubernetesJob block, similar to `blocks/orion-dolly.k8sjob.py`. Insert a reference to your own container registry, of course.
- Create a slack block so that the flow can post to your favorite slack channel. For maximum convenience, name the block `dolly-bot` so you don't need to change the flow code.
- Register the deployment by running `default.deployment.py`. Make sure to check the name of your work queue, block names etc.


Now, you can run and hope Dolly generates a nice response while you wait for the slack notification.

The default prompt is **Tell me an untrue fact about the book Hitchiker's Guide to the Galaxy**.

