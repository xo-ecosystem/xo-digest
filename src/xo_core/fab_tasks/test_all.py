from invoke import task, Collection

@task
def test_all(c):
    """
    🧪 Run all test/dev workflows: pulse.test.test_all, pulse.dev.dev
    """
    print("🧪 Running all test/dev workflows...")
    results = []
    try:
        c.run("xo-fab test.test-all")
        results.append(("test.test-all", True))
    except Exception as e:
        print(f"❌ test.test-all failed: {e}")
        results.append(("test.test-all", False))
    try:
        c.run("xo-fab dev.dev")
        results.append(("dev.dev", True))
    except Exception as e:
        print(f"❌ dev.dev failed: {e}")
        results.append(("dev.dev", False))
    print("\n📊 Test/Dev Workflow Results:")
    for name, ok in results:
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"  {status} {name}")
    passed = sum(1 for _, ok in results if ok)
    print(f"\n🎯 Overall: {passed}/{len(results)} workflows passed")
    return passed == len(results)

ns = Collection("test_all")
ns.add_task(test_all) 